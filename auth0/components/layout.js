import Container from '@material-ui/core/Container';
import Head from 'next/head'
import Header from './header'

function Layout({ user, loading = false, children }) {
  return (
    <>
      <Head>
        <title>Next.js with Auth0 and MUI</title>
      </Head>

      <Header user={user} loading={loading} />

      <main>
        <Container maxWidth="sm">{children}</Container>
      </main>

      <style jsx>{`
        .container {
          max-width: 42rem;
          margin: 1.5rem auto;
        }
      `}</style>
      <style jsx global>{`
        body {
          margin: 0;
          color: #333;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
            Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
        }
      `}</style>
    </>
  )
}

export default Layout
