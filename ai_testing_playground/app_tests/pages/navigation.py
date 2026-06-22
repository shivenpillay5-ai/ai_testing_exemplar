"""Central navigation helpers.

ALL routing between screens lives here — tests never click menu items directly. A screen gets
one `navigate_to_<screen>()` convenience method that composes the lower-level menu actions.

Adapt the selectors to your application's menu structure.
"""
from playwright.async_api import Page, expect


class NavigationPage:
    def __init__(self, page: Page):
        self.page = page

    # --- Low-level menu primitives (adapt selectors to your app) ---

    async def open_menu(self) -> None:
        """Open the main navigation menu (e.g. a hamburger button)."""
        await self.page.get_by_role("button", name="Menu").click()

    async def hover_over_module(self, module_label: str) -> None:
        """Hover a top-level module so its sub-menu expands."""
        await self.page.locator(f'span:text-is("{module_label}")').hover()

    async def click_screen(self, screen_label: str) -> None:
        """Click a screen entry inside an expanded module sub-menu."""
        item = self.page.locator(f'span:text-is("{screen_label}")')
        await item.wait_for(state="visible")
        await item.click()

    # --- Per-screen convenience methods ---
    # One method per screen. Generated tests call these, never the primitives above.

    async def navigate_to_issues(self) -> None:
        await self.open_menu()
        await self.hover_over_module("Security Master")
        await self.click_screen("Issues")
        # Confirm we arrived: the screen's grid/shell should appear.
        await expect(self.page.locator("table, [role='grid']").first).to_be_visible(timeout=30_000)
