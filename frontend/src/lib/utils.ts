// lib/utils.ts — UTILITY HELPER used by all UI components.
//
// The one function here, cn(), solves a specific Tailwind CSS problem:
//
// Problem: if you write  className="px-4 px-6"  Tailwind applies BOTH px-4 and
// px-6, which causes unpredictable results depending on CSS order. Also, when
// you combine a base class string with an override string passed as a prop, you
// can end up with duplicate or conflicting classes.
//
// Solution: cn() merges class strings intelligently:
//   1. clsx()      — flattens arrays, ignores undefined/false values
//   2. twMerge()   — removes Tailwind conflicts (keeps only the LAST value for
//                    each CSS property, e.g. px-4 + px-6 → px-6)
//
// Example:
//   cn('px-4 py-2', isLarge && 'px-6')
//   → 'py-2 px-6'   (px-4 is removed because px-6 overrides it)

import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
