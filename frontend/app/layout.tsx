import { Provider } from "@/components/ui/provider"
import { Box, Stack } from "@chakra-ui/react"
import { Sidebar } from "@/components/Sidebar"
import { Toaster } from "@/components/ui/toaster"
import AuthProvider from "./(auth)/_components/AuthProvider"

export default function RootLayout(props: { children: React.ReactNode }) {
  const { children } = props
  return (
    <html suppressHydrationWarning>
      <body>
        <Provider defaultTheme="light">
          <AuthProvider>
            <Stack direction="row" gap={0} align="stretch" minHeight="100vh">
              <Sidebar />
              <Box flex={1} overflow="auto" height="100vh">
                {children}
              </Box>
            </Stack>
            <Toaster />
          </AuthProvider>
        </Provider>
      </body>
    </html>
  )
}