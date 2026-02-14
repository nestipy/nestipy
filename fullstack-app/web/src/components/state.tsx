import React from 'react';
import type { JSX } from 'react';
import { useAppStore } from '@/store';


export const use_app_store = useAppStore;
const theme_default = {"theme": "dark", "toggle": null};
export const ThemeContext = React.createContext(theme_default);
