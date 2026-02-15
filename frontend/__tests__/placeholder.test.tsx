import React from 'react';
import { render, screen } from '@testing-library/react';

describe('placeholder test', () => {
  it('renders a basic element', () => {
    render(<div>Ghostscore frontend</div>);
    expect(screen.getByText('Ghostscore frontend')).toBeInTheDocument();
  });
});
