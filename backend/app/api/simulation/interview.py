"""Interview and environment management endpoints for simulation API."""

from flask import request, jsonify

from . import simulation_bp
from .._legacy_error_handler import legacy_api_route
from ._shared import optimize_interview_prompt, logger
from ...services.simulation_manager import SimulationManager, SimulationStatus
from ...services.simulation_runner import SimulationRunner


@simulation_bp.route('/interview', methods=['POST'])
@legacy_api_route
def interview_agent():
    """
    Interview individualAgent

    Note: This feature requires simulation to be in a running or completed state (run the simulation and wait for it to progress).

    Request (JSON):
        {
            "simulation_id": "sim_xxxx",       // Required, Simulation ID
            "agent_id": 0,                     // Required, Agent ID
            "prompt": "What do you think about this?",  // Required, Interview question
            "platform": "twitter",             // Optional, Specified platform (twitter/reddit)
                                               // When not specified: Both platforms in dual-platform simulations
            "timeout": 60                      // Optional, timeout in seconds, default 60
        }

    Return (when platform not specified, returns results from both platforms):
        {
            "success": true,
            "data": {
                "agent_id": 0,
                "prompt": "What do you think about this?",
                "result": {
                    "agent_id": 0,
                    "prompt": "...",
                    "platforms": {
                        "twitter": {"agent_id": 0, "response": "...", "platform": "twitter"},
                        "reddit": {"agent_id": 0, "response": "...", "platform": "reddit"}
                    }
                },
                "timestamp": "2025-12-08T10:00:01"
            }
        }

    Return (specified platform):
        {
            "success": true,
            "data": {
                "agent_id": 0,
                "prompt": "What do you think about this?",
                "result": {
                    "agent_id": 0,
                    "response": "I think...",
                    "platform": "twitter",
                    "timestamp": "2025-12-08T10:00:00"
                },
                "timestamp": "2025-12-08T10:00:01"
            }
        }
    """
    try:
        data = request.get_json() or {}
        
        simulation_id = data.get('simulation_id')
        agent_id = data.get('agent_id')
        prompt = data.get('prompt')
        platform = data.get('platform')  # Optional: twitter/reddit/None
        timeout = data.get('timeout', 60)
        
        if not simulation_id:
            return jsonify({
                "success": False,
                "error": "Please provide simulation_id"
            }), 400
        
        if agent_id is None:
            return jsonify({
                "success": False,
                "error": "Please provide agent_id"
            }), 400
        
        if not prompt:
            return jsonify({
                "success": False,
                "error": "Please provide prompt（Interview question）"
            }), 400
        
        # VerifyplatformParameters
        if platform and platform not in ("twitter", "reddit"):
            return jsonify({
                "success": False,
                "error": "platform Parameter can only be 'twitter' Or 'reddit'"
            }), 400
        
        # Check environment status
        if not SimulationRunner.check_env_alive(simulation_id):
            return jsonify({
                "success": False,
                "error": "Simulation environment not running or closed. Please ensure simulation is started and wait for it to progress."
            }), 400
        
        # Optimize prompt, add prefix to avoid agent calling tools
        optimized_prompt = optimize_interview_prompt(prompt)
        
        result = SimulationRunner.interview_agent(
            simulation_id=simulation_id,
            agent_id=agent_id,
            prompt=optimized_prompt,
            platform=platform,
            timeout=timeout
        )

        return jsonify({
            "success": result.get("success", False),
            "data": result
        })
        
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
        
    except TimeoutError as e:
        return jsonify({
            "success": False,
            "error": f"WaitInterviewResponse timeout: {str(e)}"
        }), 504
        
    except Exception as e:
        logger.error("InterviewFailed", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@simulation_bp.route('/interview/batch', methods=['POST'])
@legacy_api_route
def interview_agents_batch():
    """
    Batch interview multipleAgent

    Note: This feature requires simulation to be in a running or completed state.

    Request (JSON):
        {
            "simulation_id": "sim_xxxx",       // Required, Simulation ID
            "interviews": [                    // Required, Interview list
                {
                    "agent_id": 0,
                    "prompt": "Your opinion on A? What do you think?",
                    "platform": "twitter"      // Optional, interview this agent on specified platform
                },
                {
                    "agent_id": 1,
                    "prompt": "Your opinion on B? What do you think?"  // If platform not specified, use default value
                }
            ],
            "platform": "reddit",              // Optional, Default platform (overridden by each item's platform)
                                               // When not specified: Both platforms in dual-platform simulations, single platform in single-platform simulations
            "timeout": 120                     // Optional, timeout in seconds, default 120
        }

    Returns:
        {
            "success": true,
            "data": {
                "interviews_count": 2,
                "result": {
                    "interviews_count": 4,
                    "results": {
                        "twitter_0": {"agent_id": 0, "response": "...", "platform": "twitter"},
                        "reddit_0": {"agent_id": 0, "response": "...", "platform": "reddit"},
                        "twitter_1": {"agent_id": 1, "response": "...", "platform": "twitter"},
                        "reddit_1": {"agent_id": 1, "response": "...", "platform": "reddit"}
                    }
                },
                "timestamp": "2025-12-08T10:00:01"
            }
        }
    """
    try:
        data = request.get_json() or {}

        simulation_id = data.get('simulation_id')
        interviews = data.get('interviews')
        platform = data.get('platform')  # Optional: twitter/reddit/None
        timeout = data.get('timeout', 120)

        if not simulation_id:
            return jsonify({
                "success": False,
                "error": "Please provide simulation_id"
            }), 400

        if not interviews or not isinstance(interviews, list):
            return jsonify({
                "success": False,
                "error": "Please provide interviews（Interview list）"
            }), 400

        # VerifyplatformParameters
        if platform and platform not in ("twitter", "reddit"):
            return jsonify({
                "success": False,
                "error": "platform Parameter can only be 'twitter' Or 'reddit'"
            }), 400

        # Verify each interview item
        for i, interview in enumerate(interviews):
            if 'agent_id' not in interview:
                return jsonify({
                    "success": False,
                    "error": f"Interview list item{i+1}Missing agent_id"
                }), 400
            if 'prompt' not in interview:
                return jsonify({
                    "success": False,
                    "error": f"Interview list item{i+1}Missing prompt"
                }), 400
            # Verify each item's platform (if present)
            item_platform = interview.get('platform')
            if item_platform and item_platform not in ("twitter", "reddit"):
                return jsonify({
                    "success": False,
                    "error": f"Interview list item {i+1}: platform must be 'twitter' or 'reddit'"
                }), 400

        # Check environment status
        if not SimulationRunner.check_env_alive(simulation_id):
            return jsonify({
                "success": False,
                "error": "Simulation environment not running or closed. Please ensure simulation is started and wait for it to progress."
            }), 400

        # Optimize each interview item prompt, add prefix to avoid agent calling tools
        optimized_interviews = []
        for interview in interviews:
            optimized_interview = interview.copy()
            optimized_interview['prompt'] = optimize_interview_prompt(interview.get('prompt', ''))
            optimized_interviews.append(optimized_interview)

        result = SimulationRunner.interview_agents_batch(
            simulation_id=simulation_id,
            interviews=optimized_interviews,
            platform=platform,
            timeout=timeout
        )

        return jsonify({
            "success": result.get("success", False),
            "data": result
        })

    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

    except TimeoutError as e:
        return jsonify({
            "success": False,
            "error": f"Wait for batchInterviewResponse timeout: {str(e)}"
        }), 504

    except Exception as e:
        logger.error("BatchInterviewFailed", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@simulation_bp.route('/interview/all', methods=['POST'])
@legacy_api_route
def interview_all_agents():
    """
    Global interview - UseInterview all with same questionAgent

    Note: This feature requires simulation to be in a running or completed state.

    Request (JSON):
        {
            "simulation_id": "sim_xxxx",            // Required, Simulation ID
            "prompt": "What is your overall view on this?",  // Required, interview question (avoid enabling agent to use tools)
            "platform": "reddit",                   // Optional, Specified platform (twitter/reddit)
                                                    // When not specified: Both platforms in dual-platform simulations, single platform in single-platform simulations
            "timeout": 180                          // Optional, timeout in seconds, default 180
        }

    Returns:
        {
            "success": true,
            "data": {
                "interviews_count": 50,
                "result": {
                    "interviews_count": 100,
                    "results": {
                        "twitter_0": {"agent_id": 0, "response": "...", "platform": "twitter"},
                        "reddit_0": {"agent_id": 0, "response": "...", "platform": "reddit"},
                        ...
                    }
                },
                "timestamp": "2025-12-08T10:00:01"
            }
        }
    """
    try:
        data = request.get_json() or {}

        simulation_id = data.get('simulation_id')
        prompt = data.get('prompt')
        platform = data.get('platform')  # Optional: twitter/reddit/None
        timeout = data.get('timeout', 180)

        if not simulation_id:
            return jsonify({
                "success": False,
                "error": "Please provide simulation_id"
            }), 400

        if not prompt:
            return jsonify({
                "success": False,
                "error": "Please provide prompt（Interview question）"
            }), 400

        # VerifyplatformParameters
        if platform and platform not in ("twitter", "reddit"):
            return jsonify({
                "success": False,
                "error": "platform Parameter can only be 'twitter' Or 'reddit'"
            }), 400

        # Check environment status
        if not SimulationRunner.check_env_alive(simulation_id):
            return jsonify({
                "success": False,
                "error": "Simulation environment not running or closed. Please ensure simulation is started and wait for it to progress."
            }), 400

        # Optimize prompt, add prefix to avoid agent calling tools
        optimized_prompt = optimize_interview_prompt(prompt)

        result = SimulationRunner.interview_all_agents(
            simulation_id=simulation_id,
            prompt=optimized_prompt,
            platform=platform,
            timeout=timeout
        )

        return jsonify({
            "success": result.get("success", False),
            "data": result
        })

    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

    except TimeoutError as e:
        return jsonify({
            "success": False,
            "error": f"Wait for globalInterviewResponse timeout: {str(e)}"
        }), 504

    except Exception as e:
        logger.error("GlobalInterviewFailed", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@simulation_bp.route('/interview/history', methods=['POST'])
@legacy_api_route
def get_interview_history():
    """
    GetInterviewHistorical records

    Read all from simulation databaseInterviewRecord

    Request (JSON):
        {
            "simulation_id": "sim_xxxx",  // Required, Simulation ID
            "platform": "reddit",          // Optional, Platform type (reddit/twitter)
                                           // If not specified, return all history of both platforms
            "agent_id": 0,                 // Optional, Get interview history for only this agent
            "limit": 100                   // Optional, Return count, default 100
        }

    Returns:
        {
            "success": true,
            "data": {
                "count": 10,
                "history": [
                    {
                        "agent_id": 0,
                        "response": "I think...",
                        "prompt": "What do you think about this?",
                        "timestamp": "2025-12-08T10:00:00",
                        "platform": "reddit"
                    },
                    ...
                ]
            }
        }
    """
    try:
        data = request.get_json() or {}
        
        simulation_id = data.get('simulation_id')
        platform = data.get('platform')  # If not specified, return history of both platforms
        agent_id = data.get('agent_id')
        limit = data.get('limit', 100)
        
        if not simulation_id:
            return jsonify({
                "success": False,
                "error": "Please provide simulation_id"
            }), 400

        history = SimulationRunner.get_interview_history(
            simulation_id=simulation_id,
            platform=platform,
            agent_id=agent_id,
            limit=limit
        )

        return jsonify({
            "success": True,
            "data": {
                "count": len(history),
                "history": history
            }
        })

    except Exception as e:
        logger.error("Failed to get interview history", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@simulation_bp.route('/env-status', methods=['POST'])
@legacy_api_route
def get_env_status():
    """
    Get simulation environment status

    Check if simulation environment is alive (can receive interview requests).

    Request (JSON):
        {
            "simulation_id": "sim_xxxx"  // Required, Simulation ID
        }

    Returns:
        {
            "success": true,
            "data": {
                "simulation_id": "sim_xxxx",
                "env_alive": true,
                "twitter_available": true,
                "reddit_available": true,
                "message": "Environment running, ready to receive interview requests"
            }
        }
    """
    try:
        data = request.get_json() or {}
        
        simulation_id = data.get('simulation_id')
        
        if not simulation_id:
            return jsonify({
                "success": False,
                "error": "Please provide simulation_id"
            }), 400

        env_alive = SimulationRunner.check_env_alive(simulation_id)
        
        # Get more detailed status information
        env_status = SimulationRunner.get_env_status_detail(simulation_id)

        if env_alive:
            message = "Environment running, ready to receive interview requests"
        else:
            message = "Environment not running or closed"

        return jsonify({
            "success": True,
            "data": {
                "simulation_id": simulation_id,
                "env_alive": env_alive,
                "twitter_available": env_status.get("twitter_available", False),
                "reddit_available": env_status.get("reddit_available", False),
                "message": message
            }
        })

    except Exception as e:
        logger.error("Failed to get environment status", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@simulation_bp.route('/close-env', methods=['POST'])
@legacy_api_route
def close_simulation_env():
    """
    Close simulation environment
    
    Send close environment command to simulation to gracefully exit and wait for completion.

    Note: This is different from /stop. /stop terminates the simulation abruptly.
    This interface lets the simulation gracefully close the environment and exit.
    
    Request (JSON):
        {
            "simulation_id": "sim_xxxx",  // Required, Simulation ID
            "timeout": 30                  // Optional, timeout in seconds, default 30
        }
    
    Returns:
        {
            "success": true,
            "data": {
                "message": "Environment close command sent",
                "result": {...},
                "timestamp": "2025-12-08T10:00:01"
            }
        }
    """
    try:
        data = request.get_json() or {}
        
        simulation_id = data.get('simulation_id')
        timeout = data.get('timeout', 30)
        
        if not simulation_id:
            return jsonify({
                "success": False,
                "error": "Please provide simulation_id"
            }), 400
        
        result = SimulationRunner.close_simulation_env(
            simulation_id=simulation_id,
            timeout=timeout
        )
        
        # Update simulation status
        manager = SimulationManager()
        state = manager.get_simulation(simulation_id)
        if state:
            state.status = SimulationStatus.COMPLETED
            manager._save_simulation_state(state)
        
        return jsonify({
            "success": result.get("success", False),
            "data": result
        })
        
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
        
    except Exception as e:
        logger.error("Failed to close environment", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
