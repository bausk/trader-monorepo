import Head from 'next/head';

export default (props) => (
    <Head>
      <title>{ props.title || 'Livewater Trading Platform' }</title>
      <meta name='description' content={'Livewater Trading Platform'} />
      <meta name='viewport' content='width=device-width, initial-scale=1' />
      <meta charSet='utf-8' />
    </Head>
);