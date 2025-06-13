import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ url }) => {
  // For now, we'll handle auth on the client side since we're using localStorage
  // Server-side auth would require cookies or session storage
  
  return {};
};
