// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

/** Barrel for the FranchiseGuard AI component library. */

// --- foundational -----------------------------------------------------------
export { Icon } from './Icon/Icon';
export type { IconProps } from './Icon/Icon';
export { Sparkline } from './Sparkline/Sparkline';
export type { SparklineProps } from './Sparkline/Sparkline';

// --- layout ---------------------------------------------------------------
export { Screen } from './Screen/Screen';
export type { ScreenProps } from './Screen/Screen';
export { AppHeader } from './AppHeader/AppHeader';
export type { AppHeaderProps } from './AppHeader/AppHeader';
export { PageHeader } from './PageHeader/PageHeader';
export type { PageHeaderProps } from './PageHeader/PageHeader';
export { BottomNav } from './BottomNav/BottomNav';
export type { BottomNavProps } from './BottomNav/BottomNav';
export { WelcomeBanner } from './WelcomeBanner/WelcomeBanner';
export type { WelcomeBannerProps } from './WelcomeBanner/WelcomeBanner';
export { SectionHeader } from './SectionHeader/SectionHeader';
export type { SectionHeaderProps } from './SectionHeader/SectionHeader';

// --- primitives ---------------------------------------------------------
export { Button } from './primitives/Button';
export type { ButtonProps } from './primitives/Button';
export { Card, GlassCard } from './primitives/Card';
export { Chip, SeverityChip } from './primitives/Chip';
export type { ChipProps } from './primitives/Chip';
export { Skeleton, SkeletonText } from './primitives/Skeleton';
export { Sheet } from './primitives/Sheet';
export type { SheetProps } from './primitives/Sheet';
export { ProgressRing } from './primitives/ProgressRing';
export type { ProgressRingProps } from './primitives/ProgressRing';
export { RiskMeter } from './primitives/RiskMeter';
export type { RiskMeterProps } from './primitives/RiskMeter';
export { SegmentedControl } from './primitives/SegmentedControl';
export type { Segment, SegmentedControlProps } from './primitives/SegmentedControl';
export { TextField, TextArea } from './primitives/Field';
export { Avatar, Toggle, Divider, KeyValue, MetricPill } from './primitives/Misc';

// --- stats + badges ---------------------------------------------------
export { StatCard } from './StatCard/StatCard';
export type { StatCardProps } from './StatCard/StatCard';
export { StatTile } from './StatTile/StatTile';
export type { StatTileProps } from './StatTile/StatTile';
export { RiskBadge } from './RiskBadge/RiskBadge';
export type { RiskBadgeProps } from './RiskBadge/RiskBadge';
export { AlertCard } from './AlertCard/AlertCard';
export type { AlertCardProps } from './AlertCard/AlertCard';

// --- charts -----------------------------------------------------------
export { LineChart } from './charts/LineChart';
export type { LineChartProps } from './charts/LineChart';
export { BarChart } from './charts/BarChart';
export type { BarChartProps, BarGroup, Bar } from './charts/BarChart';
export { DonutChart } from './charts/DonutChart';
export type { DonutChartProps } from './charts/DonutChart';

// --- vision ---------------------------------------------------------
export { VisionScene } from './vision/VisionScene';
export type { VisionSceneProps } from './vision/VisionScene';
export { DetectionOverlay } from './vision/DetectionOverlay';
export type { DetectionOverlayProps } from './vision/DetectionOverlay';

// --- feedback -----------------------------------------------------------
export { LoadingOverlay } from './feedback/LoadingOverlay';
export type { LoadingOverlayProps } from './feedback/LoadingOverlay';

// --- inspection ---------------------------------------------------------
export { StoreSelector } from './inspection/StoreSelector';
export type { StoreSelectorProps } from './inspection/StoreSelector';
export { UploadCard } from './inspection/UploadCard';
export type { UploadCardProps } from './inspection/UploadCard';
export { ChecklistGroup } from './inspection/ChecklistGroup';
export type { ChecklistGroupProps } from './inspection/ChecklistGroup';

// --- shared domain rows -----------------------------------------------
export { ViolationCard } from './common/ViolationCard';
export type { ViolationCardProps } from './common/ViolationCard';
export { RecommendationCard } from './common/RecommendationCard';
export { TimelineList } from './common/TimelineList';
export { EvidenceGallery } from './common/EvidenceGallery';
export { StoreRow } from './common/StoreRow';
export { InspectionRow } from './common/InspectionRow';

// --- legacy (still used) ---------------------------------------------
export { UploadInspectionButton } from './UploadInspectionButton/UploadInspectionButton';
export type { UploadInspectionButtonProps } from './UploadInspectionButton/UploadInspectionButton';
export { Toast } from './Toast/Toast';
export type { ToastProps } from './Toast/Toast';
