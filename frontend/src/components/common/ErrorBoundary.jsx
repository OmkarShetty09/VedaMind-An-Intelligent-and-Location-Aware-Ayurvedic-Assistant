import { Component } from "react";

export class ErrorBoundary extends Component {
  state = { error: null };

  static getDerivedStateFromError(error) {
    return { error };
  }

  componentDidCatch(error, info) {
    console.error("ErrorBoundary:", error, info);
  }

  render() {
    if (this.state.error) {
      return (
        <div className="flex flex-col items-center gap-4 rounded-2xl border border-red-200 bg-red-50 p-8 text-center">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-red-100 text-xl">⚠️</div>
          <div>
            <p className="font-medium text-red-800">Something went wrong</p>
            <p className="mt-1 text-sm text-red-600">{this.state.error.message}</p>
          </div>
          <button
            className="rounded-xl border border-red-200 bg-white px-4 py-2 text-sm font-medium text-red-700 transition-all duration-150 hover:bg-red-50"
            onClick={() => this.setState({ error: null })}
          >
            Try again
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
