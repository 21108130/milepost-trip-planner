import { Component } from 'react';
import ErrorState from './ErrorState';

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error) {
    return { error };
  }

  componentDidCatch(error, info) {
    // eslint-disable-next-line no-console
    console.error('Unhandled UI error:', error, info);
  }

  handleRetry = () => {
    this.setState({ error: null });
  };

  render() {
    if (this.state.error) {
      return (
        <div style={{ maxWidth: 720, margin: '48px auto', padding: '0 24px' }}>
          <ErrorState
            message={this.state.error?.message || 'Something went wrong while rendering this page.'}
            onRetry={this.handleRetry}
          />
        </div>
      );
    }
    return this.props.children;
  }
}
