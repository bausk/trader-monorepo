import auth0 from '../../lib/auth0';

export default async function getToken(req, res) {
  try {
    const tokenCache = await auth0.tokenCache(req, res);
    const { accessToken } = await tokenCache.getAccessToken();
    res.status(200).json({ accessToken });
  } catch (error) {
    console.error(error)
    res.status(error.status || 500).end(error.message)
  }
}
