export const AUTH_ROLES = ["owner", "reviewer", "viewer"] as const;
export const AUTH_PERMISSIONS = ["account.read", "account.update", "audit.read", "auth.manage"] as const;

export type AuthRole = (typeof AUTH_ROLES)[number];
export type AuthPermission = (typeof AUTH_PERMISSIONS)[number];

const ROLE_PERMISSIONS: Record<AuthRole, ReadonlySet<AuthPermission>> = {
  owner: new Set(["account.read", "account.update", "audit.read", "auth.manage"]),
  reviewer: new Set(["account.read", "audit.read"]),
  viewer: new Set(["account.read"]),
};

export function permissionsForRole(role: AuthRole): AuthPermission[] {
  return [...ROLE_PERMISSIONS[role]];
}

export function roleHasPermission(role: AuthRole, permission: AuthPermission): boolean {
  return ROLE_PERMISSIONS[role].has(permission);
}

export function rolesHavePermission(roles: AuthRole[], permission: AuthPermission): boolean {
  return roles.some((role) => roleHasPermission(role, permission));
}
