"""
Integration Providers

Provider-spezifische Implementierungen.
Alle Funktionen existieren, liefern aktuell "Not connected / missing config".
"""

# Export all providers for registry
from . import (
    google, google_drive, shopify, woocommerce, hubspot, zendesk, notion, slack, whatsapp,
    booking_com, airbnb, expedia, hrs, hotels_com, trivago, agoda, padel,
    immobilienscout24, idealista, immowelt, ebay_kleinanzeigen, wohnung_de, immonet, fotocasa, habitaclia,
    microsoft_365, zoom, calendly, doxy_me, simplepractice, jane_app, epic_mychart, doctolib,
    apple_signin, icloud_calendar, icloud_drive, apple_push_notifications,
    trustpilot, tripadvisor, google_reviews, yelp, facebook_reviews
)

__all__ = [
    'google', 'google_drive', 'shopify', 'woocommerce', 'hubspot', 'zendesk', 'notion', 'slack', 'whatsapp',
    'booking_com', 'airbnb', 'expedia', 'hrs', 'hotels_com', 'trivago', 'agoda', 'padel',
    'immobilienscout24', 'idealista', 'immowelt', 'ebay_kleinanzeigen', 'wohnung_de', 'immonet', 'fotocasa', 'habitaclia',
    'microsoft_365', 'zoom', 'calendly', 'doxy_me', 'simplepractice', 'jane_app', 'epic_mychart', 'doctolib',
    'apple_signin', 'icloud_calendar', 'icloud_drive', 'apple_push_notifications',
    'trustpilot', 'tripadvisor', 'google_reviews', 'yelp', 'facebook_reviews'
]
