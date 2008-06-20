

/**
 * <p>When we detect someone doing something that causes them to join or
 * leave a channel, this strategy is invoked.
 *
 * @version $Id: ChannelJoinPartStrategy.java,v 1.2 2003/12/02 22:08:19 bryan_w Exp $
 */
public class ChannelJoinPartStrategy implements CommandProcessingStrategy {
    /**
     * Overrides method in CommandProcessingStrategy
     */
    public void execute(Command command, Chat session) {
        if (command.getCommand().equals("QUIT")) {
            partChannel(
                    session,
                    command.getSource(),
                    "[Q] " + command.getSource() + " has Quit (" + command.getArgument(0) + ")");
        } else if (command.getCommand().equals("PART")) {
            partChannel(
                    session,
                    command.getSource(),
                    "[P] "
                    + command.getSource()
                    + " has left channel "
                    + command.getArgument(0)
                    + ((command.getArgument(1) != null)
                    ? (" (" + command.getArgument(1) + ")")
                    : ""));
        } else if (command.getCommand().equals("KICK")) {
            partChannel(
                    session,
                    command.getArgument(1),
                    "[K] "
                    + command.getArgument(1)
                    + " has been kicked from channel "
                    + command.getArgument(0)
                    + " by "
                    + command.getSource()
                    + " ("
                    + command.getArgument(2)
                    + ")");
        } else if (command.getCommand().equals("JOIN")) {
            notifyUser(
                    session,
                    command.getSource(),
                    "[J] " + command.getSource() + " has joined channel " + command.getArgument(0));
            if (!session.isCurrentNick(command.getSource())) {
                session.addToNickList(command.getSource(), Chat.MODE_NONE);
            } else {
                session.setChannelName(command.getArgument(0));
            }
        }
    }

    private void notifyUser(Chat session, String target, String message) {
        if (session.isCurrentNick(target) || session.showJoinsAndParts())
            session.sendToUser(message);
    }

    private void partChannel(Chat session, String nick, String userMessage) {
        session.deleteFromNickList(nick);
        notifyUser(session, nick, userMessage);
    }

    /**
     * Overrides method in CommandProcessingStrategy
     */
    public void register() {
        Command.registerStrategy("JOIN", this);
        Command.registerStrategy("PART", this);
        Command.registerStrategy("QUIT", this);
        Command.registerStrategy("KICK", this);
    }
}
