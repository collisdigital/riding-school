import { test, expect } from '@playwright/test';

test.describe('Riders Management E2E', () => {

  test('Complete User Journey: Register -> Create School -> Manage Riders', async ({ page }) => {
    // 1. Register
    const timestamp = Date.now();
    const email = `e2e_${timestamp}@example.com`;
    const password = 'Password123!';
    const schoolName = `E2E School ${timestamp}`;

    await page.goto('/register');

    // Fill Registration
    await page.getByLabel('First Name').fill('E2E');
    await page.getByLabel('Last Name').fill('User');
    await page.getByLabel('Email Address').fill(email);
    await page.getByLabel('Password', { exact: true }).fill(password);

    // Ensure button is ready
    const createBtn = page.getByRole('button', { name: 'Create Account' });
    await expect(createBtn).toBeEnabled();
    await createBtn.click();

    // 2. Onboarding: Create School
    // Increase timeout for redirect
    await expect(page).toHaveURL(/.*\/onboarding\/create-school/, { timeout: 15000 });
    await page.getByPlaceholder('e.g. Willow Creek Equestrian').fill(schoolName);
    await page.getByRole('button', { name: 'Create School' }).click();

    // 3. Dashboard
    await expect(page).toHaveURL(/.*\/dashboard/, { timeout: 15000 });
    await expect(page.getByText(schoolName)).toBeVisible();

    // 4. Navigate to Riders
    await page.getByText('Riders', { exact: true }).click();
    await expect(page).toHaveURL(/.*\/dashboard\/riders/);

    // 5. Add Rider
    await page.getByRole('button', { name: 'Add Rider' }).click();
    await expect(page.getByText('Add New Rider')).toBeVisible();

    await page.getByLabel('First Name').fill('Alice');
    await page.getByLabel('Last Name').fill('Wonderland');
    await page.getByLabel('Email Address').fill(`alice_${timestamp}@example.com`);
    await page.getByLabel('Height (cm)').fill('160');
    await page.getByLabel('Weight (kg)').fill('50');
    // Date of Birth
    await page.getByLabel('Date of Birth').fill('2010-01-01');

    await page.getByRole('button', { name: 'Create Rider' }).click();

    // Verify Added
    await expect(page.getByText('Alice Wonderland')).toBeVisible();
    await expect(page.getByText('160 cm')).toBeVisible();
    await expect(page.getByText('50 kg')).toBeVisible();
    // Age check: 2010 -> ~14/15 years old.
    // We can just check it exists.

    // 6. Edit Rider
    // Find the row with Alice
    const row = page.getByRole('row', { name: 'Alice Wonderland' });
    await row.getByTitle('Edit').click();

    await expect(page.getByText('Edit Rider')).toBeVisible();
    await page.locator('input[value="Alice"]').fill('Alicia');
    await page.getByRole('button', { name: 'Update Rider' }).click();

    // Verify Edit
    await expect(page.getByText('Alicia Wonderland')).toBeVisible();
    await expect(page.locator('text=Alice Wonderland')).not.toBeVisible();

    // 7. Delete Rider
    // Mock dialog before click
    page.once('dialog', dialog => dialog.accept());

    const rowEdited = page.getByRole('row', { name: 'Alicia Wonderland' });
    await rowEdited.getByTitle('Delete').click();

    // Verify Deleted
    await expect(page.locator('text=Alicia Wonderland')).not.toBeVisible();
  });

});
