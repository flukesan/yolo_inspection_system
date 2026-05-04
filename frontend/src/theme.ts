import { createTheme } from '@mantine/core';

export const theme = createTheme({
  primaryColor: 'orange',
  fontFamily: 'Inter, -apple-system, sans-serif',
  defaultRadius: 'md',
  colors: {
    dark: [
      '#C9D1D9',
      '#8B949E',
      '#484F58',
      '#30363D',
      '#21262D',
      '#161B22',
      '#0D1117',
      '#0A0E13',
      '#06090C',
      '#020406',
    ],
  },
  components: {
    AppShell: { defaultProps: { bg: '#0D1117' } },
    Paper: { defaultProps: { bg: '#161B22' } },
    Card: { defaultProps: { bg: '#161B22' } },
    NavLink: { styles: { root: { borderRadius: '8px' } } },
  },
});
