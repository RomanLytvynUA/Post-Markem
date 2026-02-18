tailwind.config = {
    theme: {
        extend: {
            fontFamily: {
                sans: ['"DM Sans"', 'sans-serif'],
                serif: ['"Space Grotesk"', 'sans-serif'],
            },
            colors: {
                brand: {
                    blue: '#4D7CA2',
                    dark: '#1F272D',
                    white: '#FDFDFD',
                    alabaster: '#E2E5EA',
                    dust: '#D0D6DC',
                    slate: '#B4BEC9',
                }
            }
        }
    },
    daisyui: {
        themes: [
            {
                light: {
                    "primary": "#4D7CA2",
                    "secondary": "#6e916e",
                    "accent": "#1F272D",
                    "neutral": "#293339",
                    "base-100": "#ffffff",
                    "base-200": "#E2E5EA",
                    "info": "#4D7CA2",
                    "success": "#6e916e",
                    "warning": "#fbbf24",
                    "error": "#f87171",
                },
            },
        ],
    },
}