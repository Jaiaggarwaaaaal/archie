// Utility functions

function validateRequest(request) {
  if (!request) {
    throw new Error('Request is required');
  }
  return true;
}

function formatResponse(data) {
  return { success: true, data };
}

export { validateRequest, formatResponse };
