import { test, expect } from "@playwright/test";
import { createTodo, logout, register, uniqueEmail } from "./helpers";

test("full user journey: register, create, toggle, logout", async ({ page }) => {
  const title = `Journey todo ${Date.now()}`;

  await register(page, uniqueEmail("journey"));
  await createTodo(page, title);

  const checkbox = page.getByRole("checkbox", { name: title });
  await expect(checkbox).not.toBeChecked();
  // The UI updates optimistically, so wait for the PUT to finish before reloading
  const response = page.waitForResponse(
    (res) => res.request().method() === "PUT" && res.url().includes("/api/v1/todos/")
  );
  await checkbox.click();
  await expect(checkbox).toBeChecked();
  expect((await response).status()).toBe(200);

  // Completion is saved on the server, not only in the UI
  await page.reload();
  await expect(page.getByRole("checkbox", { name: title })).toBeChecked();

  await logout(page);
});
