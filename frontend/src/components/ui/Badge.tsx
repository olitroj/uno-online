// components/ui/Badge.tsx — SMALL LABEL / CHIP COMPONENT.
//
// A Badge is the coloured pill-shaped label used to show status information,
// for example:
//   ● online   (green)   — player is logged in
//   ● in game  (yellow)  — player is currently playing
//   ● offline  (grey)    — player is logged out
//   Friends    (green)   — accepted friend
//   Pending    (yellow)  — friend request waiting for response
//   Win / Loss (green/red) — in game history cards
//
// Variants map to colour themes:
//   default → grey    (offline, unknown)
//   success → green   (online, win, friends)
//   warning → orange  (in game, pending)
//   danger  → red     (loss, rejected)
//   info    → blue    (informational)

import { cn } from '@/lib/utils'
import type { HTMLAttributes } from 'react'

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info'
}

export function Badge({ variant = 'default', className, children, ...props }: BadgeProps) {
  const variants = {
    default: 'bg-[#2a2a4a] text-[#888899]',
    success: 'bg-[#1a3a2a] text-[#55c48a]',
    warning: 'bg-[#3a2a10] text-[#f0a030]',
    danger:  'bg-[#3a1a1a] text-[#e05555]',
    info:    'bg-[#1a2a4a] text-[#6090ff]',
  }

  return (
    <span
      className={cn('inline-block rounded-full px-2.5 py-0.5 text-xs font-semibold', variants[variant], className)}
      {...props}
    >
      {children}
    </span>
  )
}
