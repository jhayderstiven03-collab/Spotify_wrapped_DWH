export function getToken(): string | null {
    return localStorage.getItem("app_token");
  }
  
  export function isTokenExpired(token: string): boolean {
    try {
      const payload = JSON.parse(atob(token.split(".")[1]));
      return payload.exp * 1000 < Date.now();
    } catch {
      return true;
    }
  }
  
  export function logout(): void {
    localStorage.removeItem("app_token");
    window.location.href = "/login";
  }