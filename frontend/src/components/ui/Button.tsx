// components/ui/Button.tsx — REUSABLE BUTTON COMPONENT.
//
// Instead of writing the same Tailwind classes on every <button> in the app,
// we build this one component once and reuse it everywhere.
//
// It accepts two extra props on top of normal HTML button attributes:
//
//   variant — controls the colour / style:
//     'primary'   → purple background (default, main actions)
//     'secondary' → dark grey background (secondary actions)
//     'danger'    → red background (destructive actions like Delete Account)
//     'ghost'     → no background, subtle text (Logout, Cancel, Back)
//
//   size — controls padding and font size:
//     'sm' → small (used in compact lists)
//     'md' → medium (default, most buttons)
//     'lg' → large (main call-to-action buttons like Play Game)
//
// The "...props" spread passes through any standard HTML button attributes
// (onClick, disabled, type="submit", etc.) without us having to list them all.

import { cn } from '@/lib/utils'
import type { ButtonHTMLAttributes } from 'react'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
}

export function Button({ variant = 'primary', size = 'md', className, children, ...props }: ButtonProps) {
  // Base classes applied to every button regardless of variant/size
  const base = 'inline-flex items-center justify-center gap-2 rounded-lg font-semibold transition-all duration-150 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer'

  // One set of colour classes per variant
  const variants = {
    primary:   'bg-[#6c63ff] text-white hover:bg-[#5a52e0] active:scale-95',
    secondary: 'bg-[#2a2a4a] text-[#e8e8f0] hover:bg-[#3a3a5a] active:scale-95',
    danger:    'bg-[#e05555] text-white hover:bg-[#c04444] active:scale-95',
    ghost:     'bg-transparent text-[#888899] hover:text-[#e8e8f0] hover:bg-[#1a1a2e]',
  }

  // One set of spacing/font classes per size
  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base',
  }

  // cn() merges all the class strings and removes any Tailwind conflicts
  return (
    <button className={cn(base, variants[variant], sizes[size], className)} {...props}>
      {children}
    </button>
  )
}
