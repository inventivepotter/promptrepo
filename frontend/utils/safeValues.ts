// Helper functions to safely handle null/undefined values
export const safeString = (value: string | null | undefined): string => {
  return value ?? "";
};

export const safeArray = <T>(value: T[] | null | undefined): T[] => {
  return value ?? [];
};
