// src/theme/transitions.ts
// GROVIT AI — Animation & transition tokens

export const durations = {
  fast:    150,
  normal:  200,
  slow:    300,
} as const;

export const easings = {
  standard:    'cubic-bezier(0.4, 0, 0.2, 1)',
  decelerate:  'cubic-bezier(0, 0, 0.2, 1)',
  accelerate:  'cubic-bezier(0.4, 0, 1, 1)',
  sharp:       'cubic-bezier(0.4, 0, 0.6, 1)',
} as const;

/** Pre-composed transition strings */
export const transitions = {
  /** Default smooth transition for most interactive elements */
  default: `all ${durations.normal}ms ${easings.standard}`,

  /** Card hover lift */
  cardHover: `box-shadow ${durations.normal}ms ${easings.standard}, transform ${durations.normal}ms ${easings.standard}`,

  /** Sidebar collapse/expand */
  sidebar: `width ${durations.slow}ms ${easings.standard}`,

  /** Fade in/out */
  fade: `opacity ${durations.normal}ms ${easings.standard}`,

  /** Color change (background, text) */
  color: `background-color ${durations.fast}ms ${easings.standard}, color ${durations.fast}ms ${easings.standard}`,
} as const;
