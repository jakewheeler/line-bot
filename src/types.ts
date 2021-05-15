export type ActionFn = (args?: string[]) => Action;

export interface Action {
  command: string;
  fn: (args?: string[]) => string;
  description: string;
}
