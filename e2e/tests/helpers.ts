import { expect, type Page } from "@playwright/test";

export const PASSWORD = "Password@123";

export function uniqueEmail(prefix: string) {
  return `${prefix}_${Date.now()}_${Math.random().toString(36).slice(2, 8)}@test.com`;
}

export async function register(page: Page, email: string) {
  await page.goto("/register");
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password", { exact: true }).fill(PASSWORD);
  await page.getByLabel("Confirm Password").fill(PASSWORD);
  // Wait for the API call itself, so a slow first request does not hit the 5s expect timeout
  const response = page.waitForResponse("**/api/v1/auth/register");
  await page.getByRole("button", { name: "Create Account" }).click();
  expect((await response).status()).toBe(201);
  await expect(page.getByText(email)).toBeVisible();
}

export async function login(page: Page, email: string) {
  // No reload when already on /login (e.g. after logout), so the in-memory query cache is kept
  if (!page.url().endsWith("/login")) await page.goto("/login");
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password").fill(PASSWORD);
  await page.getByRole("button", { name: "Sign In" }).click();
  await expect(page.getByText(email)).toBeVisible();
}

export async function createTodo(page: Page, title: string) {
  await page.getByRole("button", { name: "Add Todo" }).click();
  await page.getByLabel("Title").fill(title);
  await page.getByRole("button", { name: "Create", exact: true }).click();
  await expect(page.getByRole("checkbox", { name: title })).toBeVisible();
}

export async function logout(page: Page) {
  await page.getByRole("button", { name: "Logout" }).click();
  await expect(page).toHaveURL(/\/login$/);
}
