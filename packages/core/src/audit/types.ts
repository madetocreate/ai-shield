import type { AuditRecord } from "../types.js";

// ============================================================
// Audit Store Interface — pluggable backends
// ============================================================

export interface AuditStore {
  /** Write a single record */
  write(record: AuditRecord): Promise<void>;
  /** Write a batch of records */
  writeBatch(records: AuditRecord[]): Promise<void>;
  /** Flush any buffered records */
  flush(): Promise<void>;
  /** Close the store */
  close(): Promise<void>;
}
