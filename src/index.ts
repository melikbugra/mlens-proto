// Re-export generated TS modules (ts-proto outputs under src/gen/mlens_proto)
// Use namespace exports to avoid duplicate symbol conflicts (e.g., DeepPartial, Exact, protobufPackage)
export * as common from './gen/mlens_proto/common';
export * as experiment from './gen/mlens_proto/experiment';
export * as events from './gen/mlens_proto/events';
