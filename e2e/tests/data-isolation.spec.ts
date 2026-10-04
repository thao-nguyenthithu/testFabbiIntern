import { test, expect } from "@playwright/test";
import { createTodo, login, logout, register, uniqueEmail } from "./helpers";

test("user B in another session cannot see user A's todo", async ({ browser }) => {
  const title = `Private todo of A ${Date.now()}`;

  const contextA = await browser.newContext();
  const pageA = await contextA.newPage();
  await register(pageA, uniqueEmail("user_a"));
  await createTodo(pageA, title);

  const contextB = await browser.newContext();
  const pageB = await contextB.newPage();
  await register(pageB, uniqueEmail("user_b"));
  await expect(pageB.getByText("No todos yet")).toBeVisible();
  await expect(pageB.getByText(title)).toHaveCount(0);

  await contextA.close();
  await contextB.close();
});

test("after A logs out, B on the same browser cannot see A's todo", async ({ page }) => {
  const title = `Private todo of A ${Date.now()}`;
  const emailB = uniqueEmail("user_b");

  // Create B first so B can log in later on the same browser
  await register(page, emailB);
  await logout(page);

  await register(page, uniqueEmail("user_a"));
  await createTodo(page, title);
  await logout(page);

  await login(page, emailB);
  await expect(page.getByText("No todos yet")).toBeVisible();
  await expect(page.getByText(title)).toHaveCount(0);
});
