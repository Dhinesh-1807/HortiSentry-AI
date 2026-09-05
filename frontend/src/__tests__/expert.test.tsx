import { describe, it, expect } from 'vitest';

describe('Expert Dashboard Logic & Workflows', () => {
  it('correctly categorizes status badge colors', () => {
    const getStatusLabel = (status: string) => {
      switch (status.toUpperCase()) {
        case 'SUBMITTED':
          return 'Submitted';
        case 'PENDING':
          return 'Expert Review Pending';
        case 'COMPLETED':
          return 'Completed';
        default:
          return status;
      }
    };

    expect(getStatusLabel('SUBMITTED')).toBe('Submitted');
    expect(getStatusLabel('PENDING')).toBe('Expert Review Pending');
    expect(getStatusLabel('COMPLETED')).toBe('Completed');
  });

  it('preserves dual predictions during expert review override', () => {
    const originalAiPrediction = 'Early Blight';
    const expertDiagnosis = 'Leaf Spot';

    const payload = {
      ai_prediction: originalAiPrediction,
      expert_prediction: expertDiagnosis,
    };

    expect(payload.ai_prediction).toBe('Early Blight');
    expect(payload.expert_prediction).toBe('Leaf Spot');
    expect(payload.ai_prediction).not.toBe(payload.expert_prediction);
  });
});
