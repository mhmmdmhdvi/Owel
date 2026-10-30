import { test, expect } from '@playwright/test';
import { execFileSync } from 'node:child_process';
import path from 'node:path';

async function fillReservation(page, email) {
  await page.getByLabel('نام و نام خانوادگی', { exact: true }).fill('E2E Test Visitor');
  await page.getByLabel('ایمیل', { exact: true }).fill(email);
  await page.getByLabel('شماره واتس‌اپ', { exact: true }).fill('+12025550123');
}

test('reservation form submits to the real API and stores the request', async ({ page }) => {
  const email = `e2e-${Date.now()}-${test.info().project.name}@example.com`;
  await page.goto('/reservation');
  await fillReservation(page, email);
  const submitted = page.waitForResponse((response) => response.url().endsWith('/api/reservations/') && response.request().method() === 'POST');
  await page.getByRole('button', { name: 'ثبت درخواست', exact: true }).click();
  expect((await submitted).status()).toBe(201);
  await expect(page.getByRole('heading', { name: 'درخواست شما ثبت شد.' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'درخواست شما ثبت شد.' })).toBeFocused();
  await expect(page.locator('main')).not.toContainText('pending');
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);

  const backend = path.resolve('../backend');
  const python = path.join(backend, process.platform === 'win32' ? '.venv/Scripts/python.exe' : '.venv/bin/python');
  const script = `from reservations.models import ReservationRequest; request = ReservationRequest.objects.get(email='${email}'); assert request.full_name == 'E2E Test Visitor'; assert request.whatsapp == '+12025550123'; request.delete()`;
  execFileSync(python, ['manage.py', 'shell', '--command', script], { cwd: backend, stdio: 'pipe' });
});

test('failed submission retains entered data and can be retried', async ({ page }) => {
  await page.route('**/api/reservations/', (route) => route.abort());
  await page.goto('/reservation');
  await fillReservation(page, 'retry@example.com');
  await page.getByRole('button', { name: 'ثبت درخواست', exact: true }).click();
  await expect(page.getByRole('alert')).toBeVisible();
  await expect(page.getByLabel('ایمیل', { exact: true })).toHaveValue('retry@example.com');
  await expect(page.getByLabel('نام و نام خانوادگی', { exact: true })).toHaveValue('E2E Test Visitor');
  await expect(page.getByRole('button', { name: 'ثبت درخواست', exact: true })).toBeEnabled();
  await expect(page.getByRole('heading', { name: 'درخواست شما ثبت شد.' })).toHaveCount(0);
});
