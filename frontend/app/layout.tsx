import type { Metadata } from "next"
import { Provider } from "@/components/ui/provider"
import { Box, Stack } from "@chakra-ui/react"
import { Sidebar } from "@/components/sidebar/Sidebar"
import { Toaster } from "@/components/ui/toaster"
import { GlobalLoadingOverlay } from "@/components/GlobalLoadingOverlay"

export const metadata: Metadata = {
  icons: "/favicon.svg",
}

export default function RootLayout(props: { children: React.ReactNode }) {
  const { children } = props
  return (
    <html suppressHydrationWarning>
      <body>
        <Provider defaultTheme="light">
            <Stack direction="row" gap={0} align="stretch" minHeight="100vh">
              <Sidebar />
              <Box flex={1} overflow="auto" height="100vh">
                {children}
              </Box>
            </Stack>
            <Toaster />
            <GlobalLoadingOverlay />
        </Provider>
      </body>
    </html>
  )
}