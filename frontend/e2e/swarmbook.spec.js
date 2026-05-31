import { test, expect } from '@playwright/test';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

test.describe('Swarmbook Studio E2E', () => {
  test('Wizard Flow - cannot proceed without Title', async ({ page }) => {
    await page.goto('/swarmbook');
    // Navigate to new wizard
    await page.click('text=New Test');
    
    // Attempt to proceed without filling fields
    const nextBtn = page.locator('button.primary-btn');
    await nextBtn.click();
    
    // Expect validation error
    const errorBanner = page.locator('.validation-alert');
    await expect(errorBanner).toBeVisible();
    await expect(errorBanner).toContainText('Please fix the following before continuing');
  });

  test('Wizard Flow - Full Upload and Simulation stub', async ({ page }) => {
    test.setTimeout(120000); // 2 minutes, file uploading and moving takes time
    
    await page.goto('/swarmbook/wizard/test_project_123');

    // Step 1: Basics
    await expect(page.locator('#step1-heading')).toContainText('What are we testing?');
    await page.fill('#s1-project', 'test_project_123');
    await page.fill('#s1-title', 'Automated Test Book');
    await page.fill('#s1-author', 'Automated Tester');
    await page.fill('#s1-genre', 'Fiction');
    await page.selectOption('#s1-contentType', 'novel');
    await page.selectOption('#s1-bookType', 'fiction');
    await page.click('button.primary-btn.next-btn');

    // Step 2: Upload
    await expect(page.locator('#step2-heading')).toContainText('What should the system read?');
    const fileInput = page.locator('input[type="file"]');
    const filePath = path.join(__dirname, '..', '..', 'tests', 'fixtures', 'sample_fiction_excerpt.md');
    await fileInput.setInputFiles(filePath);
    
    // Wait for the uploaded file display to appear (confirms parsing is completed)
    await expect(page.locator('.selected-file-display')).toBeVisible({ timeout: 15000 });
    
    await page.click('button.primary-btn.next-btn');

    // Step 3: Intent
    await expect(page.locator('#step3-heading')).toContainText('Who is this for and what should it achieve?');
    await page.fill('#s3-targetReader', 'Fans of suspense');
    await page.fill('#s3-testGoal', 'Test the ending pacing');
    await page.fill('#s3-blurb', 'A short excerpt about Mara arriving with a secret. Detailed blurb description must be long enough to pass validation.');
    await page.click('button.primary-btn.next-btn');

    // Step 4: Evidence Review
    await expect(page.locator('#step4-heading')).toBeVisible({ timeout: 25000 });
    await expect(page.locator('#step4-heading')).toContainText('Did the system understand your work correctly?');
    // For e2e, we skip waiting for the real backend pack generation and just click continue if the button is enabled
    // The button might be disabled until "Regenerate" finishes. Let's wait for it.
    await expect(page.locator('button.primary-btn.next-btn')).toBeEnabled({ timeout: 25000 });
    await page.click('button.primary-btn.next-btn');

    // Step 5: Simulation Setup
    await expect(page.locator('#step5-heading')).toContainText('Which readers and editors should test this?');
    await page.click('button.primary-btn.next-btn');

    // Step 6: Review & Run
    await expect(page.locator('#step6-heading')).toContainText('What will happen now?');
    
    // Check elements exist
    await expect(page.locator('text=Automated Test Book')).toBeVisible();
  });
});
