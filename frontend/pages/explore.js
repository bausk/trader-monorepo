import React, { useCallback } from 'react';

import { observer } from 'mobx-react';

import SourcesList from 'components/Sources/SourcesList';
import ResourcesList from 'components/Resources/ResourcesList';

function Explore() {
  return (
    <>
      <SourcesList />
      <ResourcesList />
    </>
  )
}

Explore.getInitialProps = async ({ req }) => {
    return {
    };
};

export default observer(Explore);
