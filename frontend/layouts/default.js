import React from 'react';
import Link from 'next/link'
import Meta from '../components/meta';
import Navbar from '../components/navbar';
import '../styles/styles.sass';

export default ({ children, meta }) => (
  <div>
    <Meta props={meta} />
    <Navbar />
    {children}
  </div>
);
