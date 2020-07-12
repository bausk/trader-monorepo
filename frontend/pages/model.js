import React, { useCallback } from 'react';
import useSWR from 'swr';
import { useRouter } from 'next/router';
import TableContainer from "@material-ui/core/TableContainer";
import Paper from "@material-ui/core/Paper";
import Table from "@material-ui/core/Table";
import TableBody from "@material-ui/core/TableBody";
import TableCell from "@material-ui/core/TableCell";
import TableHead from "@material-ui/core/TableHead";
import TableRow from "@material-ui/core/TableRow";
import Button from "@material-ui/core/Button";
import IconButton from "@material-ui/core/IconButton";
import AddIcon from "@material-ui/icons/Add";
import RefreshIcon from "@material-ui/icons/Refresh";
import { observer } from 'mobx-react';
import TableLayout from 'components/layouts/TableLayout';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import Switch from '@material-ui/core/Switch';
import NewStrategyModal from 'components/Modals/NewStrategyModal';
import { useStores } from 'components/rootStore';
import { DeleteButton } from 'components/buttons';
import b from 'api/backendRoutes';
import f from 'api/frontendRoutes';

function ListStrategies() {
  const { sourcesStore, resourcesStore, authStore } = useStores();
  const router = useRouter();

  const { data: resourcesList } = useSWR(
    b.RESOURCES,
    resourcesStore.resources.listResource
  );

  const { data, error, mutate } = useSWR(
    b.STRATEGIES,
    async () => {
      return await sourcesStore.strategies.list();
    }
  );
  const newModal = router.asPath === f.MODEL_NEW;

  const onAdd = useCallback(async () => {
    return router.push(f.MODEL, f.MODEL_NEW);
  }, [router]);

  const onSubmit = useCallback(async (result) => {
    const newStrategy = {
      id: undefined,
      config_json: JSON.stringify({
      }),
      ...result
    };
    mutate(async (prev) => [...prev, newStrategy], false);
    mutate(sourcesStore.strategies.add(newStrategy));
  }, []);

  const onClose = useCallback(() => {
    return router.push(f.MODEL);
  }, [router]);

  const onRefresh = useCallback(async () => {
    mutate();
  }, []);
  const { user, loading } = authStore;
  const rows = data || [];
  if (!loading && !user) {
    return null;
  }
  
  const handleChange = useCallback(async (newValue) => {
    mutate(
      prev => prev.map(p => (p.id === newValue.id ? newValue : p)),
      false
    );
    await sourcesStore.strategies.putIsLive(newValue);
    mutate();
  }, [sourcesStore]);

  return (
    <TableLayout
      title="Strategies"
      toolbar={() => (
        <>
          <NewStrategyModal
            open={newModal}
            onClose={onClose}
            onSubmit={onSubmit}
            resources={resourcesList}
          />
          <IconButton
            edge="start"
            onClick={onAdd}
            color="inherit"
            aria-label="menu"
          >
            <AddIcon />
          </IconButton>
          <IconButton
            onClick={onRefresh}
            color="inherit"
            aria-label="menu"
          >
            <RefreshIcon />
          </IconButton>
        </>
      )}
    >
      <TableContainer component={Paper}>
      <Table aria-label="simple table">
        <TableHead>
          <TableRow>
            <TableCell>Strategy ID</TableCell>
            <TableCell>Name</TableCell>
            <TableCell>Type</TableCell>
            <TableCell>Connected Sources</TableCell>
            <TableCell align="right">Operations</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {rows.map((row, i) => (
            <TableRow key={i}>
              <TableCell component="th" scope="row">
                <Button
                  onClick={() => router.push(`${f.MODEL}/[id]`, `${f.MODEL}/${row.id}`)}
                >
                  {row.id}
                </Button>
              </TableCell>
              <TableCell>
                {row.name}
              </TableCell>
              <TableCell>
                {row.typename}
              </TableCell>
              <TableCell>
                {row?.resource_model?.name || 'None'}
              </TableCell>
              <TableCell align="right">
                <SwitchIsLive element={row} onChange={handleChange} />
                <DeleteButton element={row} mutate={mutate} store={sourcesStore.strategies} />
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  </TableLayout>
  )
}

const SwitchIsLive = ({ element, onChange }) => {
  const isLive = !!element.live_session_id;
  const onSwitch = useCallback(
    (e) => {
      const newValue = {
        ...element,
        live_session_id: isLive ? null : true
      }
      onChange(newValue);
    },
    [element]
  );
  return (
    <FormControlLabel
      value="start"
      control={<Switch
        color="primary"
        checked={isLive}
        onChange={onSwitch}
      />}
      label={isLive? "Active" : "Inactive"}
      labelPlacement="start"
    />
  );
};

export default observer(ListStrategies);
