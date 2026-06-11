// components/ui/Card.tsx — DARK BOX CONTAINER for UI sections (NOT the UNO playing card).
//
// This "Card" is purely a layout container — a dark rounded box with a border
// used to group related content on the home page (profile box, friend entries, etc.)
//
// It exports two components:
//   Card      — the outer container box
//   CardTitle — a heading <h2> styled to sit inside a Card
//
// The "...props" spread passes through any HTML div attributes (onClick, style, etc.)
// and lets callers add extra classes via the className prop (merged by cn()).
//
// Example usage:
//   <Card>
//     <CardTitle>My Friends</CardTitle>
//     <p>friend list goes here</p>
//   </Card>

import { cn } from '@/lib/utils'
import type { HTMLAttributes } from 'react'

export function Card({ className, children, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn('rounded-xl border border-[#2a2a4a] bg-[#1a1a2e] p-4', className)}
      {...props}
    >
      {children}
    </div>
  )
}

export function CardTitle({ className, children, ...props }: HTMLAttributes<HTMLHeadingElement>) {
  return (
    <h2 className={cn('mb-3 text-base font-semibold text-[#e8e8f0]', className)} {...props}>
      {children}
    </h2>
  )
}
