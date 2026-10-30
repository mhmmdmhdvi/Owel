import { test, expect } from '@playwright/test';

test('navigation reaches services, with no horizontal scrolling', async ({ page, isMobile }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { level: 1 })).toBeVisible();
  if (isMobile) {
    const toggle = page.getByRole('button', { name: 'فهرست' });
    await toggle.click();
    await expect(toggle).toHaveAttribute('aria-expanded', 'true');
    await page.getByRole('navigation', { name: 'فهرست اصلی' }).getByRole('link', { name: 'خدمات' }).click();
    await expect(toggle).toHaveAttribute('aria-expanded', 'false');
  } else {
    await page.getByRole('navigation', { name: 'فهرست اصلی' }).getByRole('link', { name: 'خدمات' }).click();
  }
  await expect(page).toHaveURL(/#services$/);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
});

test('service details open and close using the keyboard', async ({ page }) => {
  await page.goto('/');
  const details = page.getByRole('button', { name: /کلاس‌های آموزشی Owel/ });
  await details.focus();
  await page.keyboard.press('Enter');
  await expect(details).toHaveAttribute('aria-expanded', 'true');
  await expect(page.locator('#services').getByRole('region', { name: 'کلاس‌های آموزشی Owel' })).toBeVisible();
  await page.keyboard.press('Enter');
  await expect(details).toHaveAttribute('aria-expanded', 'false');
  await expect(page.locator('#services').getByRole('region', { name: 'کلاس‌های آموزشی Owel' })).toBeHidden();
});

test('mobile menu can be dismissed with Escape and restores focus', async ({ page, isMobile }) => {
  test.skip(!isMobile, 'Mobile navigation only');
  await page.goto('/');
  const toggle = page.getByRole('button', { name: 'فهرست' });
  await toggle.click();
  await page.keyboard.press('Escape');
  await expect(toggle).toHaveAttribute('aria-expanded', 'false');
  await expect(toggle).toBeFocused();
});

test('hero photograph covers the whole section behind its content', async ({ page }) => {
  await page.goto('/');
  const section = page.locator('#home');
  const photo = section.locator('img');
  await expect(photo).toBeVisible();
  const heroBounds = await section.boundingBox();
  const photoBounds = await photo.boundingBox();
  const viewport = page.viewportSize();
  expect(heroBounds.x).toBe(0);
  expect(heroBounds.width).toBe(viewport.width);
  expect(photoBounds.x).toBe(heroBounds.x);
  expect(photoBounds.y).toBe(heroBounds.y);
  expect(photoBounds.width).toBe(heroBounds.width);
  expect(photoBounds.height).toBe(heroBounds.height);
  expect(await photo.evaluate((image) => getComputedStyle(image).objectFit)).toBe('cover');
});

test('floating up arrow appears after scrolling and returns to the top', async ({ page }) => {
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.goto('/');
  const backToTop = page.getByRole('button', { name: 'بازگشت به بالا' });
  await expect(backToTop).toBeHidden();
  await page.evaluate(() => window.scrollTo(0, 1000));
  await expect(backToTop).toBeVisible();
  await backToTop.click();
  await expect.poll(() => page.evaluate(() => window.scrollY)).toBe(0);
  await expect(backToTop).toBeHidden();
});
