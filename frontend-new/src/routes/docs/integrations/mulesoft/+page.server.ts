import type { PageServerLoad } from './$types';
import { readFile } from 'fs/promises';
import { join } from 'path';
import { marked } from 'marked';

export const load: PageServerLoad = async () => {
  try {
    const filePath = join(process.cwd(), 'static', 'docs', 'integrations', 'mulesoft-integration-guide.md');
    const markdown = await readFile(filePath, 'utf-8');
    const htmlContent = marked(markdown);
    
    return {
      htmlContent
    };
  } catch (error) {
    console.error('Error loading documentation:', error);
    return {
      htmlContent: '<h1>Error loading documentation</h1><p>Could not load the Mulesoft integration guide.</p>'
    };
  }
};
