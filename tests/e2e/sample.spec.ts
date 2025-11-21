import { test, expect } from '@playwright/test';

// Test: homepage renders
test('homepage has title', async ({ page }) => {
  await page.goto('/');
  await expect(page.locator('text=Content Processing POC')).toBeVisible();
});

// Test: upload flow (requires backend running and accessible at /api)
test('upload document and get result', async ({ page, request }) => {
  // navigate
  await page.goto('/');

  // simulate file upload via API (use a small text file)
  const fileContent = 'Dummy file content';
  const formData = new FormData();
  const blob = new Blob([fileContent], { type: 'text/plain' });
  formData.append('file', blob, 'sample.txt');

  const res = await request.post('/api/ingest', { body: formData });
  expect(res.ok()).toBeTruthy();
  const body = await res.json();
  const docId = body.doc_id;
  expect(docId).toBeTruthy();

  // Poll for results
  for (let i = 0; i < 10; i++) {
    const r = await request.get(`/api/results/${docId}`);
    if (r.ok()) {
      const data = await r.json();
      expect(data.doc_id).toBe(docId);
      return;
    }
    await new Promise((res) => setTimeout(res, 1000));
  }
  throw new Error('Result not available in time');
});
