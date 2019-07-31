import Link from 'next/link';
import Layout from '../layouts/default'
import { withAuthSync } from '../utils/auth';

export default withAuthSync((props) => {
  const { isLoggedIn } = props;
  return (
    <Layout>
      <section className="section">
        <div className="container">
          <h1 className="title">Hello! You can&nbsp;
            {
              !isLoggedIn &&
              <Link prefetch href="/login">
                <a>Log In</a>
              </Link>
            }
            {
              isLoggedIn &&
              <Link prefetch href="/logout">
                <a>Log Out</a>
              </Link>
            }
          </h1>
        </div>
      </section>
    </Layout>
  )
}
);