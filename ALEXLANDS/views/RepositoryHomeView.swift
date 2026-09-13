import SwiftUI

struct RepositoryHomeView: View {
    @Environment(\.appLanguage) private var language

    let onOpenSettings: () -> Void
    let onOpenLogs: () -> Void

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 20) {
                    Spacer().frame(height: 100)
                    AppLogo()
                    Text(language.text("onboarding.welcome_title"))
                        .font(.title)
                        .fontWeight(.bold)
                        .foregroundStyle(.white)
                    Text(language.text("home.subtitle"))
                        .font(.subheadline)
                        .foregroundStyle(.white.opacity(0.8))
                }
                .frame(maxWidth: .infinity)
            }
            .scrollContentBackground(.hidden)
            .background(
                Image("AppBackground")
                    .resizable()
                    .scaledToFill()
                    .ignoresSafeArea()
            )
            .navigationTitle("ALEXLANDS")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                AppUtilityToolbar(
                    language: language,
                    onOpenSettings: onOpenSettings,
                    onOpenLogs: onOpenLogs
                )
            }
        }
    }

}
