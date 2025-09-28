import { createSystem, defaultConfig, defineConfig } from "@chakra-ui/react"

const config = defineConfig({
  theme: {
    tokens: {
      colors: {
        primary: {
          50: { value: "#F0F2F0" }, // lightest shade
          100: { value: "#E8ECE8" }, // lightest - made even lighter
          200: { value: "#CAD2C5" }, // lightest
          300: { value: "#84A98C" }, // lighter
          400: { value: "#52796F" }, // a bit light
          500: { value: "#52796F" }, // a bit light
          600: { value: "#354F52" }, // secondary
          700: { value: "#354F52" }, // secondary
          800: { value: "#2F3E46" }, // primary dark
          900: { value: "#1E2A30" }, // primary dark
          950: { value: "#0A0F13" }, // darker shade for accents - made even darker
        },
      },
    },
    semanticTokens: {
      colors: {
        primary: {
          solid: { value: "{colors.primary.600}" }, // secondary
          contrast: { value: "{colors.primary.100}" }, // lightest
          fg: { value: "{colors.primary.800}" }, // primary dark
          muted: { value: "{colors.primary.200}" }, // lighter
          subtle: { value: "{colors.primary.300}" }, // lighter
          emphasized: { value: "{colors.primary.400}" }, // a bit light
          focusRing: { value: "{colors.primary.500}" }, // a bit light
        },
        // Set the default color palette to primary
        bg: {
          DEFAULT: {
            value: { _light: "{colors.primary.50}", _dark: "{colors.primary.950}" },
          },
          subtle: {
            value: { _light: "{colors.primary.50}", _dark: "{colors.primary.900}" },
          },
          muted: {
            value: { _light: "{colors.primary.100}", _dark: "{colors.primary.800}" },
          },
          emphasized: {
            value: { _light: "{colors.primary.200}", _dark: "{colors.primary.700}" },
          },
          inverted: {
            value: { _light: "{colors.primary.950}", _dark: "{colors.primary.50}" },
          },
        },
        fg: {
          DEFAULT: {
            value: { _light: "{colors.primary.950}", _dark: "{colors.primary.50}" },
          },
          subtle: {
            value: { _light: "{colors.primary.800}", _dark: "{colors.primary.200}" },
          },
          muted: {
            value: { _light: "{colors.primary.700}", _dark: "{colors.primary.300}" },
          },
          emphasized: {
            value: { _light: "{colors.primary.900}", _dark: "{colors.primary.100}" },
          },
          inverted: {
            value: { _light: "{colors.primary.50}", _dark: "{colors.primary.950}" },
          },
        },
        border: {
          DEFAULT: {
            value: { _light: "{colors.primary.200}", _dark: "{colors.primary.700}" },
          },
        },
      },
    },
  },
})

export const system = createSystem(defaultConfig, config)