import { createSystem, defaultConfig, defineConfig, defineRecipe } from "@chakra-ui/react"

const buttonRecipe = defineRecipe({
  variants: {
    variant: {
      solid: {
        bg: "{colors.primary.solid}",
        color: "{colors.bg}",
        _hover: {
          color: "{colors.bg.inverted}",
          bg: "{colors.primary.emphasized}",
        },
        _active: {
          bg: "{colors.primary.fg}",
        },
      },
      outline: {
        borderWidth: "1px",
        borderColor: "{colors.primary.solid}",
        color: "{colors.primary.solid}",
        bg: "transparent",
        _hover: {
          bg: "{colors.bg.subtle}",
          borderColor: "{colors.primary.emphasized}",
          color: "{colors.primary.emphasized}",
        },
        _active: {
          bg: "{colors.bg.muted}",
          borderColor: "{colors.primary.fg}",
        },
      },
      ghost: {
        color: "{colors.primary.solid}",
        bg: "transparent",
        _hover: {
          bg: "{colors.bg.subtle}",
        },
        _active: {
          bg: "{colors.bg.muted}",
        },
      },
      link: {
        color: "{colors.link.DEFAULT}",
        bg: "transparent",
        fontWeight: "medium",
        padding: 0,
        height: "auto",
        textDecoration: "underline",
        _hover: {
          color: "{colors.link.hover}",
          textDecoration: "underline",
        },
        _active: {
          color: "{colors.link.visited}",
        },
      },
    },
    textColor: {
      primary: { color: "{colors.text.primary}" },
      secondary: { color: "{colors.text.secondary}" },
      tertiary: { color: "{colors.text.tertiary}" },
      disabled: { color: "{colors.text.disabled}" },
      inverse: { color: "{colors.text.inverse}" },
      success: { color: "{colors.text.success}" },
    },
  },
})

const config = defineConfig({
  globalCss: {
    "body, :root": {
      color: "{colors.fg.DEFAULT}",
      bg: "{colors.bg.DEFAULT}",
    },
    // Add a more specific rule to ensure it overrides
    "body &, :root &": {
      color: "{colors.fg.DEFAULT}",
    },
  },
  theme: {
    textStyles: {
      DEFAULT: {
        color: "{colors.fg.DEFAULT}",
      },
    },
    tokens: {
      colors: {
        primary: {
          50: { value: "#F0F2F0" }, // lightest shade
          100: { value: "#E8ECE8" }, // lightest - made even lighter
          200: { value: "#CAD2C5" }, // lightest
          300: { value: "#84A98C" }, // lighter
          400: { value: "#52796F" }, // a bit light
          500: { value: "#4A6F65" }, // medium-light
          600: { value: "#3F5F57" }, // medium
          700: { value: "#354F52" }, // secondary
          800: { value: "#2F3E46" }, // primary dark
          900: { value: "#12181C" }, // primary dark - closer to 950
          950: { value: "#0A0F13" }, // darker shade for accents - made even darker
        },
      },
    },
    recipes: {
      button: buttonRecipe,
    },
    semanticTokens: {
      colors: {
        primary: {
          solid: { value: { _light: "{colors.primary.700}", _dark: "{colors.primary.200}" } }, // secondary
          contrast: { value: { _light: "{colors.primary.100}", _dark: "{colors.primary.900}" } }, // lightest / darkest
          fg: { value: { _light: "{colors.primary.800}", _dark: "{colors.primary.200}" } }, // primary dark / primary light
          muted: { value: { _light: "{colors.primary.200}", _dark: "{colors.primary.700}" } }, // lighter / darker
          subtle: { value: { _light: "{colors.primary.300}", _dark: "{colors.primary.600}" } }, // lighter / secondary
          emphasized: { value: { _light: "{colors.primary.300}", _dark: "{colors.primary.500}" } }, // a bit light
          focusRing: { value: { _light: "{colors.primary.500}", _dark: "{colors.primary.400}" } }, // a bit light
        },
        // Background colors
        bg: {
          DEFAULT: {
            value: { _light: "{colors.primary.50}", _dark: "{colors.primary.950}" },
          },
          subtle: {
            value: { _light: "{colors.primary.100}", _dark: "{colors.primary.900}" },
          },
          muted: {
            value: { _light: "{colors.primary.200}", _dark: "{colors.primary.800}" },
          },
          emphasized: {
            value: { _light: "{colors.primary.300}", _dark: "{colors.primary.600}" },
          },
          inverted: {
            value: { _light: "{colors.primary.950}", _dark: "{colors.primary.50}" },
          },
        },
        // Foreground/Text colors
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
        // Text-specific color tokens
        text: {
          primary: {
            value: { _light: "{colors.primary.950}", _dark: "{colors.primary.50}" },
          },
          secondary: {
            value: { _light: "{colors.primary.800}", _dark: "{colors.primary.200}" },
          },
          tertiary: {
            value: { _light: "{colors.primary.700}", _dark: "{colors.primary.300}" },
          },
          disabled: {
            value: { _light: "{colors.primary.400}", _dark: "{colors.primary.600}" },
          },
          placeholder: {
            value: { _light: "{colors.primary.500}", _dark: "{colors.primary.500}" },
          },
          inverse: {
            value: { _light: "{colors.primary.50}", _dark: "{colors.primary.950}" },
          },
          success: {
            value: { _light: "{colors.primary.600}", _dark: "{colors.primary.400}" },
          },
        },
        // Heading colors
        heading: {
          DEFAULT: {
            value: { _light: "{colors.primary.900}", _dark: "{colors.primary.100}" },
          },
          subtle: {
            value: { _light: "{colors.primary.800}", _dark: "{colors.primary.200}" },
          },
          muted: {
            value: { _light: "{colors.primary.700}", _dark: "{colors.primary.300}" },
          },
        },
        // Link colors
        link: {
          DEFAULT: {
            value: { _light: "{colors.primary.600}", _dark: "{colors.primary.400}" },
          },
          hover: {
            value: { _light: "{colors.primary.700}", _dark: "{colors.primary.300}" },
          },
          visited: {
            value: { _light: "{colors.primary.800}", _dark: "{colors.primary.500}" },
          },
        },
        // Border colors
        border: {
          DEFAULT: {
            value: { _light: "{colors.primary.200}", _dark: "{colors.primary.700}" },
          },
          subtle: {
            value: { _light: "{colors.primary.100}", _dark: "{colors.primary.800}" },
          },
          emphasized: {
            value: { _light: "{colors.primary.300}", _dark: "{colors.primary.600}" },
          },
        },
        // Shadow colors
        shadow: {
          DEFAULT: {
            value: { _light: "rgba(30, 42, 48, 0.1)", _dark: "rgba(10, 15, 19, 0.3)" },
          },
          subtle: {
            value: { _light: "rgba(30, 42, 48, 0.05)", _dark: "rgba(10, 15, 19, 0.2)" },
          },
          emphasized: {
            value: { _light: "rgba(30, 42, 48, 0.2)", _dark: "rgba(10, 15, 19, 0.4)" },
          },
        },
      },
    },
  },
})

export const system = createSystem(defaultConfig, config)