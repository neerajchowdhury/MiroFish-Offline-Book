# Reader Swarm Output Schema Templates

## Persona

```json
{
  "agent_id": "bt-emotional-03",
  "platform_home": "booktok",
  "genre_preferences": ["literary sci-fi", "time travel"],
  "review_style": "emotional-confessional",
  "patience_level": "medium",
  "dnf_triggers": ["slow opening", "unclear stakes"],
  "delight_triggers": ["moral ambiguity", "grief payoff"],
  "influence_score": 0.42
}
```

## Platform Reaction

```json
{
  "agent_id": "rd-plotlogic-04",
  "platform": "reddit",
  "round": 2,
  "rating": 3,
  "dnf_probability": 0.31,
  "sentiment": "mixed-negative",
  "claim": "The time rules need clearer causality.",
  "friction": ["plot logic", "exposition"],
  "praise": ["premise"],
  "reply_likelihood": 0.77,
  "confidence": 0.58
}
```

## Final Scorecard

```json
{
  "average_rating_range": [3.4, 4.1],
  "polarization": "medium-high",
  "dnf_risk": 0.29,
  "controversy_risk": 0.22,
  "viral_potential": 0.64,
  "positioning_accuracy": 0.71,
  "top_revision_priorities": ["clarify stakes earlier", "reduce chapter 3 exposition"]
}
```
