import { test, expect } from '@playwright/test';
import { execFileSync } from 'node:child_process';
import path from 'node:path';

const backend = path.resolve('../backend');
const python = path.join(backend, process.platform === 'win32' ? '.venv/Scripts/python.exe' : '.venv/bin/python');

test('staff logs in, reviews a reservation, and logs out', async ({ page }) => {
  const username = `staff-${Date.now()}-${test.info().project.name}`;
  const email = `${username}@example.com`;
  const setup = `from django.contrib.auth import get_user_model; from django.contrib.auth.models import Permission; from reservations.models import ReservationRequest; u=get_user_model().objects.create_user('${username}',password='E2E-test-password',is_staff=True); u.user_permissions.add(*Permission.objects.filter(codename__in=['view_reservationrequest','change_reservationrequest'])); ReservationRequest.objects.create(full_name='E2E Staff Visitor',email='${email}',whatsapp='+12025550123')`;
  execFileSync(python, ['manage.py', 'shell', '--command', setup], { cwd: backend, stdio: 'pipe' });
  try {
    await page.goto('/staff');
    await page.getByLabel('نام کاربری', { exact: true }).fill(username);
    await page.getByLabel('رمز عبور', { exact: true }).fill('E2E-test-password');
    await page.getByRole('button', { name: 'ورود', exact: true }).click();
    await expect(page.getByRole('heading', { name: 'درخواست‌های رزرو', exact: true })).toBeVisible();
    await page.getByLabel('جست‌وجو', { exact: true }).fill(email);
    await page.getByRole('button', { name: 'جست‌وجو', exact: true }).click();
    const row = page.getByRole('row').filter({ hasText: email });
    await expect(row).toBeVisible();
    await row.getByRole('button', { name: 'جزئیات' }).click();
    const dialog = page.getByRole('dialog');
    await expect(dialog).toBeVisible();
    await dialog.getByLabel('بررسی شده', { exact: true }).check();
    await dialog.getByLabel('یادداشت داخلی', { exact: true }).fill('E2E review');
    await dialog.getByRole('button', { name: 'ذخیره', exact: true }).click();
    await expect(dialog).toBeHidden();
    await expect(row).toContainText('بررسی شده');
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    await page.getByRole('button', { name: 'خروج', exact: true }).click();
    await expect(page.getByRole('button', { name: 'ورود', exact: true })).toBeVisible();
    await expect(page.getByText(email, { exact: true })).toHaveCount(0);
    // Losing connectivity must never leave customer data on screen after logout.
    await page.getByLabel('نام کاربری', { exact: true }).fill(username);
    await page.getByLabel('رمز عبور', { exact: true }).fill('E2E-test-password');
    await page.getByRole('button', { name: 'ورود', exact: true }).click();
    await expect(page.getByRole('table')).toBeVisible();
    await page.route('**/api/staff/logout/', (route) => route.abort());
    await page.getByRole('button', { name: 'خروج', exact: true }).click();
    await expect(page.getByRole('button', { name: 'ورود', exact: true })).toBeVisible();
    await expect(page.getByRole('table')).toHaveCount(0);
  } finally {
    const cleanup = `from django.contrib.auth import get_user_model; from reservations.models import ReservationRequest; from staff_portal.models import LoginGuard; ReservationRequest.objects.filter(email='${email}').delete(); get_user_model().objects.filter(username='${username}').delete(); LoginGuard.objects.filter(username='${username}').delete()`;
    execFileSync(python, ['manage.py', 'shell', '--command', cleanup], { cwd: backend, stdio: 'pipe' });
  }
});

test('unapproved staff access shows login and no reservation data', async ({ page }) => {
  await page.goto('/staff');
  await expect(page.getByLabel('نام کاربری', { exact: true })).toBeVisible();
  await expect(page.getByRole('table')).toHaveCount(0);
  await page.getByLabel('نام کاربری', { exact: true }).fill(`invalid-${Date.now()}`);
  await page.getByLabel('رمز عبور', { exact: true }).fill('incorrect-password');
  await page.getByRole('button', { name: 'ورود', exact: true }).click();
  await expect(page.getByRole('alert')).toBeVisible();
  await expect(page.getByRole('table')).toHaveCount(0);
});
