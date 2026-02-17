import { apiClient } from '../lib/api'

describe('apiClient.downloadProfilePdf', () => {
  it('should throw if profileId is missing', async () => {
    await expect(apiClient.downloadProfilePdf('')).rejects.toThrow()
  })
  // Note: Integration test for actual download requires backend running and a valid profileId
})
