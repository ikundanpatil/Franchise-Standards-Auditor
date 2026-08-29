// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

/**
 * FranchiseGuard AI — mobile-first field companion for franchise compliance.
 *
 * The app ships its own splash → login → dashboard flow, app header, bottom
 * navigation and page transitions, so it renders as the full app surface
 * rather than inside <AppLayout> (the shell's desktop frame). All screen
 * state lives in <FranchiseGuardApp>, which mounts the navigator, the toast
 * host and the scoped design tokens.
 */

import React from 'react';
import type { ShellAppProps } from 'shell';
import { FranchiseGuardApp } from './app/FranchiseGuardApp';
import { MANAGER } from './data/manager';

const App: React.FC<ShellAppProps> = ({ identity }) => (
	<FranchiseGuardApp managerName={identity?.displayName ?? MANAGER.name} />
);

export default App;
