/**
 * Client Wrapper for Root Layout
 * Contains global styles and providers with conditional floating chat button
 */

"use client";

import { ReactNode } from 'react';
import ConditionalFloatingChat from './ConditionalFloatingChat';

export default function ClientRootWrapper({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <ConditionalFloatingChat>
      {children}
    </ConditionalFloatingChat>
  );
}