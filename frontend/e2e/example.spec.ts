import { test, expect } from '@playwright/test';

test('homepage has title and opens', async ({ page }) => {
  await page.goto(process.env.NEXT_PUBLIC_API_URL ? process.env.NEXT_PUBLIC_API_URL : 'http://localhost:3000');
  // Basic smoke check: page loads
  await expect(page).toHaveTitle(/Ghostscore|Ghost/i);
});
