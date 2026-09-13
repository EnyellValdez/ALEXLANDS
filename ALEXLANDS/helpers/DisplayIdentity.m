#import "DisplayIdentity.h"
#import <CommonCrypto/CommonDigest.h>

// Public project identity. Upstream credits remain in THIRD_PARTY_NOTICES.md.
static NSString *decodedAttributionString(void) {
    return @"https://github.com/EnyellValdez/EnyellSystems";
}

NSURL *DisplayIdentityAttributionURL(void) {
    NSString *s = decodedAttributionString();
    if (![s hasPrefix:@"https://"]) return nil;
    return [NSURL URLWithString:s];
}

NSString *DisplayIdentityAttestationToken(void) {
    // Stable display token derived from the public URL and current bundle ID.
    NSString *bid = [[NSBundle mainBundle] bundleIdentifier] ?: @"com.enyell.ts.app2";
    NSString *base = decodedAttributionString();
    NSString *raw = [NSString stringWithFormat:@"%@|%@", bid, base];
    NSData *d = [raw dataUsingEncoding:NSUTF8StringEncoding];
    unsigned char hash[CC_SHA256_DIGEST_LENGTH];
    CC_SHA256(d.bytes, (CC_LONG)d.length, hash);
    NSMutableString *hex = [NSMutableString stringWithCapacity:CC_SHA256_DIGEST_LENGTH * 2];
    for (int i = 0; i < 8; i++) [hex appendFormat:@"%02x", hash[i]];
    return [hex copy];
}
