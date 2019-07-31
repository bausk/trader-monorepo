import Layout from '../layouts/default';
import React from 'react';
import { connect } from 'react-redux';
import { withAuthSync } from '../utils/auth';
import { REQUEST_LOGIN } from '../components/Login/Login.actions';


class Login extends React.Component {
  constructor (props) {
    super(props);
    this.state = { token: '', error: '' };
  }

  handleChange = (event) => {
    this.setState({ token: event.target.value })
  };

  handleSubmit = async (event) => {
    event.preventDefault();
    const accessToken = this.state.token;
    try {
      await this.props.login(accessToken);
    } catch(error) {
      console.warn(error);
    }

  };

  render() {
    return (
      <Layout>
        <div className='login'>
          <form onSubmit={this.handleSubmit}>
            <label htmlFor='token'>Access Token</label>

            <input
              type='text'
              id='token'
              name='token'
              value={this.state.token}
              onChange={this.handleChange}
            />

            <button type='submit'>Login</button>

            <p className={`error ${this.state.error && 'show'}`}>
              {this.state.error && `Error: ${this.state.error}`}
            </p>
          </form>
        </div>
        <style jsx>{`
          .login {
            max-width: 340px;
            margin: 0 auto;
            padding: 1rem;
            border: 1px solid #ccc;
            border-radius: 4px;
          }
          form {
            display: flex;
            flex-flow: column;
          }
          label {
            font-weight: 600;
          }
          input {
            padding: 8px;
            margin: 0.3rem 0 1rem;
            border: 1px solid #ccc;
            border-radius: 4px;
          }
          .error {
            margin: 0.5rem 0 0;
            display: none;
            color: brown;
          }
          .error.show {
            display: block;
          }
        `}</style>
      </Layout>
    );
  }
}

const mapDispatchToProps = {
  login: REQUEST_LOGIN.action
};

export default connect(null, mapDispatchToProps)(Login);
