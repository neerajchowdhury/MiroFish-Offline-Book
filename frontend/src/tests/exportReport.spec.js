import { describe, it, expect } from 'vitest';
import { buildMarkdownContent } from '../utils/exportReport';

describe('exportReport utility', () => {
  it('builds a valid markdown string with report and sessionContext', () => {
    const mockReport = {
      title: 'Test Book',
      project_id: 'test_proj_123',
      scorecard: {
        score_readiness: 75,
        score_commercial: 80,
        score_literary: 70
      },
      summary: 'This is a test verdict.'
    };
    const mockSession = { projectId: 'test_proj_123' };
    
    const result = buildMarkdownContent(mockReport, mockSession);
    expect(result).toContain('# Swarmbook Report: Test Book');
    expect(result).toContain('This is a test verdict.');
    expect(result).toContain('This report is synthesized from a deterministic simulation run');
  });

  it('handles missing title gracefully', () => {
    const mockReport = {
      project_id: 'test_proj_456'
    };
    const mockSession = {};
    const result = buildMarkdownContent(mockReport, mockSession);
    expect(result).toContain('# Swarmbook Report: test_proj_456');
  });

  it('returns empty string if no report provided', () => {
    const result = buildMarkdownContent(null, {});
    expect(result).toBe('');
  });
});
